# Coherence-graph lens

The industry-blank differentiator. Detects cross-artifact drift across six
structured sub-graphs: description, version, capability, cross-reference,
example, spec-conformance. Catches the README ↔ `package.json` ↔ About ↔
marketplace ↔ topics ↔ CHANGELOG drift that motivated `code-ultrareview`'s
rewrite.

## Dispatch protocol

One `Explore` subagent per coherence-graph run. The subagent invokes the
orchestrator:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/coherence/run.py" \
  --repo "<repo>" [--include-prose] --json
```

The orchestrator runs each sub-graph extractor, applies `.coherence-ignore`
allowlists, and emits a unified findings list. Extractors are pure Python 3
stdlib — no network calls in default mode. Sub-graphs that depend on `gh`
(description, topics) degrade gracefully when `gh` is unavailable: the
header notes the skip; the sub-graph emits no findings.

## The six sub-graphs

### 1. description

Compares structured description fields across:

- `package.json` → `.description`
- `.claude-plugin/marketplace.json` → `.metadata.description`
- `gh repo view --json description` → `.description`
- `skills/<name>/SKILL.md` → frontmatter `description` (single-skill repos only)

Default mode compares structured fields only. `--include-prose` extends the
comparison to the README's first paragraph (high false-positive — opt-in).
GitHub topics are deliberately excluded: they are keyword tags, not
descriptions, and pairing them with descriptions produces false positives
without catching real drift. Per-plugin descriptions and per-skill SKILL.md
descriptions are pinned within their own plugin (planned, post-MVP);
cross-plugin comparison would be noise.

Equality uses case-insensitive normalization. Each disagreeing pair surfaces
as one finding (severity `Medium`, confidence 90).

### 2. version

Compares all present version sources, split into two roles:

- **Manifest sources** (declared intent — bump first, in a PR):
  - `package.json` → `.version`
  - `.claude-plugin/marketplace.json` → `.metadata.version`
  - `CHANGELOG.md` → most recent `^## [vV]?\d+\.\d+\.\d+` header
- **Release sources** (published reality — bump after merge):
  - `git tag -l --sort=-v:refname | head -1`
  - `gh release list -L 1 --json tagName`

Comparison is semver-aware (`compare_versions` in `_common.py` — `major.minor.patch`
tuple compare; pre-release / build suffixes stripped). The conventional flow is
**manifest leads release**: between the version bump and the tag/release, manifest
sources are ahead of release sources, and that is not drift. The sub-graph
emits a finding only when:

- A release source is **ahead** of a manifest source (someone tagged but didn't bump the manifest — real drift).
- Two manifest sources or two release sources **disagree** with each other (real inconsistency, regardless of direction).

Each emitted finding has severity `High` and confidence 95. The default — no
finding for `manifest > release` — replaces the prior "allowlist via
`.coherence-ignore`" workaround for normal pre-release prep. The allowlist
still works for genuine exceptions (e.g., a tag intentionally divorced from
the manifest stream).

### 3. capability

Parses README sections matching `Features`, `Commands`, `Skills`, or
`Workstreams` and attempts to resolve each listed item to a file, function,
or flag reference. An item with zero supporting references surfaces as one
finding (severity `Medium`, confidence 70 — heuristic).

Resolution attempts: `Glob` against `<item>` as a partial path; `Grep` for
`<item>` as a function or class; flag-shaped tokens (`--<item>` or `-<item>`)
matched against `argparse`/`parse_args` patterns.

### 4. cross-reference

Resolves every relative link in `.md` files at the repo root and in
`skills/*/`:

- File-existence checks for relative paths (`./foo.md`, `../bar/baz.md`).
- Anchor-existence checks for `#section` references (heading present in
  target file).
- Skill-name references — `/forge`, `/apex` etc. — resolved against
  `.claude-plugin/marketplace.json` → `.plugins[].skills`.

A missing target surfaces as one finding (severity `High`, confidence 95).

### 5. example

Parses fenced code blocks marked `bash`, `sh`, or `shell`. For each command,
extracts the program + flags and matches the flags against the program's
script source via:

- `argparse.add_argument("-x", "--xxx", ...)` patterns
- `parse_args` shell idioms (`while getopts`, manual case statements)

A flag appearing in the example but not in the program's parser surfaces as
one finding (severity `Medium`, confidence 80).

### 6. spec-conformance

The full spec-conformance lens (`WebFetch` + cache + grammar inference) is a
later iteration. The current entrypoint is a stub: it detects normative-spec
mentions in diff/README/`CLAUDE.md` using the normative-spec regex and emits a
deferred placeholder
finding (severity `Low`, confidence 50, recommendation pointing to the spec-conformance iteration pass).

## Finding schema

Each finding matches the canonical lens schema:

```json
{
  "lens": "coherence-graph",
  "sub_graph": "description | version | capability | cross-reference | example | spec-conformance",
  "severity": "High | Medium | Low",
  "location": "path:line | path | (cross-source)",
  "finding": "What is wrong",
  "recommendation": "What to do",
  "confidence": 0
}
```

`sub_graph` is the coherence-graph-specific field — readers can filter by
which sub-graph fired. The orchestrator preserves it through aggregation
(kept as `meta.sub_graph` on the canonical finding row).

## `.coherence-ignore` format

Per-repo allowlist at repo root. Minimal YAML subset — keys are sub-graph
names, values are graph-specific allowlists.

```yaml
# Allowlist version divergence between tag and package.json
# (unreleased work — tag is intentionally ahead)
version:
  ignore_pairs:
    - git-tag:package.json

# README mentions a legacy CLI tool we no longer ship
capability:
  ignore_items:
    - legacy-cli

# Two description sources legitimately use different wording
description:
  ignore_pairs:
    - package.json:gh-about

# Internal docs link to specs not under version control
cross-reference:
  ignore_paths:
    - docs/internal/*.md
```

The parser supports comments (`#`), nested mappings (2-space indent), and
flat lists (`-` items). No quotes, no anchors, no multi-doc streams — keep
the file readable, the parser tiny. The full grammar lives in
`scripts/coherence/_common.py` (`load_ignore`).

## `--include-prose` semantics

Opt-in extension to the description sub-graph. When set, the README's first
paragraph (between the H1 and the first H2 or fenced block) is normalized
(strip markdown, lowercase, collapse whitespace) and compared against the
structured description fields. High false-positive rate — repos with rich
README intros frequently diverge from terse `package.json` descriptions
without that being a coherence bug. Gated explicitly for this reason.

The `--include-prose` finding inherits severity `Low` (downgraded from the
structured Medium) to reflect the heuristic nature.

## Graceful degradation

- `gh` CLI missing → description sub-graph skips the GitHub About + topics
  sources; emits a header note (not a finding).
- `package.json` missing → description + version sub-graphs skip it silently
  (no failure; absence is not divergence).
- `CHANGELOG.md` missing → version sub-graph skips that source.
- `marketplace.json` missing → description + cross-reference sub-graphs skip
  it (non-skills repos work fine without one).
- `git` missing or repo unborn → version sub-graph skips the tag source.

The orchestrator's exit code is always `0` when extractors complete (even
when sub-graphs emit zero findings). Non-zero exit means a hard failure
(missing script, invalid `.coherence-ignore`, repo path doesn't exist).

## Caveats

- Description case-insensitive comparison normalizes whitespace but not
  punctuation. `Foo. Bar.` and `Foo, Bar` would diverge — accepted.
- Version `v1.2.3` vs `1.2.3` is treated as equal (leading `v` stripped).
- Capability resolution is best-effort. A README listing "Configurable
  retries" has nothing to match — the heuristic confidence (70) reflects
  this.
- The example sub-graph parses only `bash`/`sh`/`shell` fences. Examples
  marked `console`, `terminal`, or unlabelled are skipped — false negatives
  acceptable at MVP.
- Spec-conformance is intentionally stubbed for now. The full lens
  (`WebFetch` + 7-day ETag cache + grammar inference) is a later iteration.

## Fixtures

Coherence-graph fixtures live under
`tests/code-ultrareview/fixtures/coherence-graph/`, one directory per case:

| Fixture | Expected findings |
|---------|-------------------|
| `clean-repo/` | none |
| `clean-structured-divergent-prose/` | none in default mode; one with `--include-prose` |
| `description-divergence/` | one finding (description sub-graph) |
| `description-divergence-ignored/` | none (allowlisted in `.coherence-ignore`) |
| `version-mismatch/` | one finding (version sub-graph) |
| `broken-cross-skill-reference/` | one finding (cross-reference sub-graph) |
| `broken-example/` | one finding (example sub-graph) |
