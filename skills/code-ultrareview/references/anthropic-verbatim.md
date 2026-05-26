# Anthropic verbatim primitives

Verbatim review primitives carried from Anthropic's official `code-review` plugin. Used by:

- Phase 3 axis reviewers — score each finding against the 0-100 rubric.
- Phase 4 Haiku validators — re-score sub-80 findings and re-check the CLAUDE.md citation.
- Phase 5 synthesis — tier classification (`Important` / `Nit` / `Pre-existing`).

**Drift surveillance.** Every block below carries a `## Source` line + `Last verified: 2026-05-26`. The test `tests/code-ultrareview/test_anthropic_verbatim.py` enforces byte-for-byte parity against the upstream source file when that file is present. Quarterly re-verification: open the source, diff against the block, update if needed, bump the date.

Upstream typos (e.g. "compily") are preserved deliberately — the contract is byte-for-byte parity, not stylistic improvement on top of Anthropic's wording.

---

## 0-100 Confidence Rubric

Score each issue on a scale from 0-100, indicating the level of confidence:

   a. 0: Not confident at all. This is a false positive that doesn't stand up to light scrutiny, or is a pre-existing issue.
   b. 25: Somewhat confident. This might be a real issue, but may also be a false positive. The agent wasn't able to verify that it's a real issue. If the issue is stylistic, it is one that was not explicitly called out in the relevant CLAUDE.md.
   c. 50: Moderately confident. The agent was able to verify this is a real issue, but it might be a nitpick or not happen very often in practice. Relative to the rest of the PR, it's not very important.
   d. 75: Highly confident. The agent double checked the issue, and verified that it is very likely it is a real issue that will be hit in practice. The existing approach in the PR is insufficient. The issue is very important and will directly impact the code's functionality, or it is an issue that is directly mentioned in the relevant CLAUDE.md.
   e. 100: Absolutely certain. The agent double checked the issue, and confirmed that it is definitely a real issue, that will happen frequently in practice. The evidence directly confirms this.

### Source

- `sources/claude-plugins-official/plugins/code-review/commands/code-review.md` — step 5 rubric (a-e)
- Last verified: 2026-05-26

---

## HIGH SIGNAL review criteria

5 parallel agents review the change independently:

   a. Agent #1: Audit the changes to make sure they compily with the CLAUDE.md. Note that CLAUDE.md is guidance for Claude as it writes code, so not all instructions will be applicable during code review.
   b. Agent #2: Read the file changes in the pull request, then do a shallow scan for obvious bugs. Avoid reading extra context beyond the changes, focusing just on the changes themselves. Focus on large bugs, and avoid small issues and nitpicks. Ignore likely false positives.
   c. Agent #3: Read the git blame and history of the code modified, to identify any bugs in light of that historical context
   d. Agent #4: Read previous pull requests that touched these files, and check for any comments on those pull requests that may also apply to the current pull request.
   e. Agent #5: Read code comments in the modified files, and make sure the changes in the pull request comply with any guidance in the comments.

### Source

- `sources/claude-plugins-official/plugins/code-review/commands/code-review.md` — step 4 agents (a-e)
- Last verified: 2026-05-26

---

## False-positive taxonomy

Examples of false positives:

- Pre-existing issues
- Something that looks like a bug but is not actually a bug
- Pedantic nitpicks that a senior engineer wouldn't call out
- Issues that a linter, typechecker, or compiler would catch (eg. missing or incorrect imports, type errors, broken tests, formatting issues, pedantic style issues like newlines). No need to run these build steps yourself -- it is safe to assume that they will be run separately as part of CI.
- General code quality issues (eg. lack of test coverage, general security issues, poor documentation), unless explicitly required in CLAUDE.md
- Issues that are called out in CLAUDE.md, but explicitly silenced in the code (eg. due to a lint ignore comment)
- Changes in functionality that are likely intentional or are directly related to the broader change
- Real issues, but on lines that the user did not modify in their pull request

### Source

- `sources/claude-plugins-official/plugins/code-review/commands/code-review.md` — examples of false positives
- Last verified: 2026-05-26

---

## Agent assumption rule

- Do not check build signal or attempt to build or typecheck the app. These will run separately, and are not relevant to your code review.

### Source

- `sources/claude-plugins-official/plugins/code-review/commands/code-review.md` — notes section
- Last verified: 2026-05-26

---

## Application in code-ultrareview

- **Phase 3 axis reviewers** — every axis subagent prompt cites the 0-100 rubric verbatim AND the false-positive taxonomy. Findings scored 0-100. Out-of-scope concerns (security, runtime perf, flaky tests) are excluded from axis output and surface in the closing "What I did NOT check" section.
- **Phase 4 Haiku validators** — receive a sub-80 finding + the rubric + the CLAUDE.md snippet. Re-score 0-100. Demote with reason when the cited CLAUDE.md rule is not actually present in `claude_md_chain`.
- **Phase 5 synthesis** — tier classification reads the score. `Important` = confidence ≥ 80 AND severity High/Medium. `Nit` = ≥ 80 AND Low. `Pre-existing` = `finding.pre_existing == true`. Verdict (Ship / Fix-then-ship / Needs work) ignores sub-80 — the A2 contract surfaces them in `### ⚠️ Unverified` without affecting the verdict.

## Why these blocks

| Block | Why carry it |
|-------|--------------|
| 0-100 rubric | Reproducibility — every validator scores against the same yardstick. The 80-threshold gate (`scripts/synthesis_core.py:CONFIDENCE_THRESHOLD`) is meaningful only if the rubric is stable. |
| HIGH SIGNAL criteria | Sets the bar for what an axis is allowed to flag — large bugs and direct CLAUDE.md violations, not stylistic nitpicks. |
| False-positive taxonomy | The 8-class list is the explicit "don't flag this" contract. Linter-territory issues, intentional changes, and pre-existing problems are silenced at source instead of cluttering the report. |
| Agent assumption rule | The skill is read-only judgment review. Build/typecheck run separately in CI; this rule keeps Phase 3 focused on judgment, not execution. |
