# Lens: Rules compliance (key `rules`)

New violations of the rule hierarchy introduced by the diff. Cite the
exact rule line verbatim. A rule written as guidance for *writing* code
is not always a review criterion — apply judgment. Pre-existing
violations on unchanged lines are out of scope. If no rule file exists
anywhere, this lens is skipped — see `lenses.md` § *Graceful
degradation*.

## Repo-kind branches

No branches — rule files are repo-agnostic; the lens reads the rule
hierarchy uniformly across all `repo_kind` values surfaced by the audit
phase.
