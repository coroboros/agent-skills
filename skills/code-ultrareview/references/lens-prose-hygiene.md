# Lens: Prose hygiene (key `prose-hygiene`)

Reviews shared prose touched by the session — PR body + title (when a PR
is open), every commit between the resolved base and HEAD, and
user-facing `*.md` files in the diff. Ships a portable baseline; layers
user/project rules on top via standard Claude Code discovery; project
rules win on conflict. Closes the public-prose hygiene axis the other
lenses do not cover.

## Inputs

| Input | Source | When |
|-------|--------|------|
| PR body + title | `scripts/fetch_pr_meta.sh` → `gh pr view` | When `gh` is on PATH, authenticated, and an open PR exists for the current branch |
| Commit messages | `scripts/fetch_commits.sh` → `git log <base>..HEAD` | Always (when ≥1 commit exists between base and HEAD) |
| Prose files in the diff | Diff file list, filtered through the scope rule below | Always |

Both shell scripts emit machine-parseable output (`RESULT: key=value`
lines plus NUL-delimited commit records) so the lens subagent can parse
without round-tripping JSON through bash.

## Scope

**In scope** — public-displayed prose, anything a reader sees after merge.

- PR body and PR title
- Commit subjects and bodies
- `README.md`, `README.mdx`
- `CHANGELOG.md`, `RELEASE-NOTES.md`
- Any `*.md` / `*.mdx` under `docs/`
- Any `*.md` / `*.mdx` at repo root (excluded files below take precedence)

**Out of scope** — model-instruction files, not shared prose deliverables.
The scope filter strips these from the diff file list before any check
runs.

- `SKILL.md`
- `CLAUDE.md`
- `evals.json`
- Anything under `.claude/rules/`
- Anything under `skills/<name>/` (skill source — `/skill-creator` owns
  prose quality there)

Scope-exclusion regex (canonical, mirrored in
`scripts/check_prose_hygiene.py::SCOPE_EXCLUDE_RE`):

```
(?:^|/)(?:SKILL\.md|CLAUDE\.md|evals\.json|\.claude/rules/|skills/[^/]+/)
```

## Portable baseline

The skill ships these defaults so the lens works on any repo. The
orchestrator layers discovered user/project rules on top (see *Layered
discovery* below).

### Length budgets

| Artifact | Section | Budget |
|----------|---------|--------|
| PR body | Summary bullets | ≤ 5 |
| PR body | Test plan items | ≤ 8 |
| PR body | Total non-blank lines | ≤ 80 (soft) · > 150 fails |
| Commit | Subject | ≤ 72 chars |
| Commit | Body line | ≤ 100 chars wrap |
| Commit | Body total | ≤ 20 non-blank lines |

### AI vocabulary

`delve`, `tapestry`, `intricate`, `pivotal`, `testament`, `underscore`,
`crucial`, `garner`, `showcase`, `additionally`, `moreover`,
`furthermore`, `indeed`. One finding per occurrence, capped at three per
term per artifact (noise floor).

### Em-dash density

> 1 em-dash per 100 words → finding (only when the artifact has ≥ 100
words; shorter prose escapes the check).

### Internal leaks

| Pattern | Severity | Reason |
|---------|----------|--------|
| `/Users/<name>/`, `/home/<name>/`, `C:\Users\<name>\` | High | Local path leak |
| `<user>@<gmail|icloud|yahoo|hotmail|outlook|proton|me|aol>.<tld>` | High | Personal email |
| `<Name>'s-MacBook…` style hostnames | High | Machine identifier |

### Authoring-process traces

| Pattern | Severity | Reason |
|---------|----------|--------|
| `(?:~|$HOME|/Users/<name>|/home/<name>)/(?:\.claude/)?brand-voices?/` | High | Authoring-tool path leak |
| `(?:~|$HOME|/Users/<name>|/home/<name>)/<seg>/BRAND-VOICE(?:-[A-Z_]+)?\.md` | High | Authoring-tool filename in path context |
| `maintainer-specific` | High | Internal-author/user split |
| `maintainer's (path|tool|config|voice|rules)` | High | Internal-author/user split |
| `(internal|private) (voice|rules|tooling|tool|config|path)` | High | Internal-tooling reference |

Path-context anchoring keeps the check tight — plain mentions of a
public skill by name (e.g. a README row describing the `brand-voice`
skill) do not fire; only paths and possessive constructions tied to the
authoring environment trigger. The check runs on the same surfaces as
internal-leak: PR title, PR body, commit body, prose files in the diff.

### AI signature footers

| Pattern | Severity |
|---------|----------|
| `Co-Authored-By: Claude` | High |
| `Co-Authored-By: Cursor` | High |
| `🤖 Generated with` | High |
| `Generated with [Cc]laude` (line start) | High |
| `As an AI…` (line start) | High |

### Defensive negations

| Pattern | Severity | Reason |
|---------|----------|--------|
| `(?:The|This|Our)\s+(?:lens|skill|script|tool|check|detector|orchestrator)\s+never\s+(?:names?|mentions?|references?|uses?|exposes?|hardcodes?|leaks?)` | Medium | Skill-subject negation |
| `no\s+\w+-specific\s+\w+` | Medium | Defensive scoping |
| `never\s+(?:names?|mentions?|references?)\s+(?:any|a)\s+\w+` | Medium | Anchored negation |

Mandate allowlist — phrases on the same line suppress any defensive
match: uppercase `\bNEVER\b`, `never fail silently`, `never break the
public API`, `never aborts`, `never advertises`, `never silent-drop`.
Fenced code blocks, HTML comments, and table cells are skipped before
matching — quoted prose and structural cells are not body assertions.
Anchor: `~/.claude/rules/writing.md` § "Assert positively. Reserve
negation for real constraints (`NEVER commit secrets`)."

### Rule-restatement / silent-compliance

Bullet/checklist lines that restate a rule the body claims to follow —
the generalized form of the silent-compliance pattern. Detected via
specific anchors (`No <something> footer`, `Per the rule`, `As instructed
by`, `Followed the convention`, `Silent compliance`). Section headers
like `## Test plan` do **not** match — only the bullets do.

Also flagged: filler test-plan items (`test thoroughly`, `verify nothing
broke`, `make sure it works`) — replace with enumerable, reproducible
verification steps.

### Conventional Commits

Subject must match `^(<type>)(\(<scope>\))?!?: <description>` where
`<type>` is one of `feat`, `fix`, `docs`, `chore`, `refactor`, `test`,
`perf`, `ci`, `build`, `style`, `revert`.

Severity depends on **adoption auto-detect** — `cc_is_adopted(repo_root)`
returns true when **any** of:

1. A `.commitlintrc*` or `commitlint.config.*` file exists at repo root.
2. `commitlint` or `@commitlint/*` is listed in `package.json`
   dependencies or devDependencies.
3. ≥ 50% of the last 20 commit subjects match the CC pattern.

When adopted → non-CC commit subjects are 🟠 Medium. When not adopted →
🟢 Low / informational ("optional — adopt CC by adding a
`.commitlintrc*`").

## Layered discovery

The orchestrator composes the merged rule set in this order; project
rules win on conflict per the standard precedence model:

1. **Skill-baked baseline** — the rules above.
2. **User-global rules** — `~/.claude/rules/{writing,git-conventions,privacy}.md`.
3. **Project rules** — `CLAUDE.md`, `.claude/rules/*.md` at repo root.
4. **Per-repo overrides** — `.claude/rules/*.md` (already covered by 3).

`discover_rules(repo_root)` returns the discovered file paths so the
report header can surface a one-line `Prose rules: <list>` (or `Prose
rules: baseline only` when none are found). Discovery is path-based and
does not parse rule content — content interpretation is the subagent's
job at dispatch time.

## Dispatch

The lens runs as a read-only `Explore` subagent in the parallel fan-out.
It receives:

- the resolved `base`/`target` (or "dirty tree"),
- the rule-hierarchy paths (same set the `rules` lens receives),
- the prose-files list from the diff (already scope-filtered upstream),
- the absolute path to `scripts/check_prose_hygiene.py`,
- the absolute paths to `scripts/fetch_pr_meta.sh` and
  `scripts/fetch_commits.sh`.

The subagent executes (read-only):

1. `bash scripts/fetch_pr_meta.sh` → parse `RESULT:` lines and body block.
2. `bash scripts/fetch_commits.sh` → write to a temp file (commits arrive
   NUL-delimited; piping through `--commits-file <path>` keeps the wire
   format intact).
3. `python3 scripts/check_prose_hygiene.py --pr-body-file <tmp>
   --pr-title "<…>" --commits-file <tmp> --prose-file <p1> --prose-file
   <p2> --repo-root <root>` → parse the JSON findings.
4. Apply any project-rule overrides discovered via
   `discover_rules(repo_root)`. When a discovered rule narrows or
   extends a baseline category, prefer the project rule and note the
   source in the finding's `meta.rule_source`.
5. Return the findings in the canonical lens schema (`lens`, `severity`,
   `location`, `finding`, `recommendation`, `confidence`).

## Opt-out

The lens is **always-on**. The `--no-prose-hygiene` flag (parsed by the
dispatcher from `$ARGUMENTS`) skips the dispatch entirely; the
`📋 Lens summary` row reads `— skipped (--no-prose-hygiene)`. No opt-in
flag exists — the lens runs by default on every invocation, mirroring
the other always-on lenses.

## Graceful degradation

| Condition | Behavior |
|-----------|----------|
| `gh` not on PATH | `fetch_pr_meta.sh` emits `pr_found=false`; lens runs on commits + prose only |
| `gh` present but not authenticated | Same as above — graceful skip |
| No open PR for current branch | Same as above |
| No commits between base and HEAD | Lens runs on the PR body and prose only |
| No prose files in the diff | Lens runs on the PR body and commits only |
| All four input channels empty | Lens returns `clean` with no findings |

The lens never aborts the review — every degradation is announced in the
finding set (or the absence thereof) and surfaced in the Lens summary
row.

## Deferred routing

When `humanize-en` is installed on the user's machine
(`~/.claude/skills/humanize-en/` or `~/.agents/skills/humanize-en/`), the
synthesizer appends a `→ defer to /humanize-en` line under each
`ai-vocabulary` and `em-dash-density` finding. Otherwise the finding
stands on its own. This routing lives in `references/skill-routing.md`;
this lens just emits the findings.
