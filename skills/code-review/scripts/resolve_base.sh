#!/usr/bin/env bash
#
# resolve_base.sh — resolve the review base for the code-review skill.
#
# Determines, deterministically, what a clean-tree review diffs against,
# via an explicit precedence ladder. The skill prints the chosen rule in
# the report header so the review target is never silent. The "repo-declared
# base" precedence is owned by the skill (it reads CLAUDE.md / .claude/rules
# in-context and passes the result via -b); this script is pure git topology.
#
# Usage:
#   resolve_base.sh [-b <ref>]
#
# Ladder (first match wins):
#   1. explicit            -b <ref> given
#   2. feature-merge-base  HEAD != default branch → merge-base(HEAD, default)
#   3. default-upstream    on default branch with an upstream → @{upstream}
#   4. default-tag         on default, no upstream, a tag exists → last tag
#   5. default-prev        on default, no upstream, no tag → HEAD~1
#   6. default-initial     single commit → the empty tree (all files as added)
#
# Ref rungs (explicit, default-upstream, default-tag) resolve `base` to
# `merge-base <ref> HEAD` so it is always a diffable ancestor (or the empty
# tree for default-initial). The skill therefore uses two-dot
# `git diff <base> <target>` uniformly — no three-dot, no tree-vs-commit
# edge case, no noise from commits the base gained in parallel.
#
# Exit:
#   0   resolved
#   2   unresolvable (no commits, detached HEAD, shallow w/o merge-base)
#
# Always emits a final `RESULT:` line on stdout for parseability:
#   RESULT: base=<ref> target=<ref> rule=<rung>
#   RESULT: rule=unresolvable hint=<text>            (exit 2)

set -euo pipefail

BASE_OVERRIDE=""
while getopts ":b:" opt; do
  case "$opt" in
    b) BASE_OVERRIDE="$OPTARG" ;;
    *) echo "RESULT: rule=unresolvable hint=usage: resolve_base.sh [-b <ref>]"; exit 2 ;;
  esac
done

TARGET="HEAD"

# No commits yet — nothing to diff.
if ! git rev-parse --verify -q HEAD >/dev/null 2>&1; then
  echo "RESULT: rule=unresolvable hint=no commits in repository"
  exit 2
fi

# Rung 1 — explicit override (skill passes a repo-declared base here too).
if [[ -n "$BASE_OVERRIDE" ]]; then
  base=$(git merge-base "$BASE_OVERRIDE" HEAD 2>/dev/null || echo "$BASE_OVERRIDE")
  echo "RESULT: base=$base target=$TARGET rule=explicit"
  exit 0
fi

# Detect the default branch (short name).
detect_default() {
  local d
  d=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null) || true
  if [[ -n "${d:-}" ]]; then
    echo "${d#origin/}"
    return
  fi
  if git show-ref --verify --quiet refs/heads/main; then echo main; return; fi
  if git show-ref --verify --quiet refs/heads/master; then echo master; return; fi
  d=$(git config --get init.defaultBranch 2>/dev/null) || true
  echo "${d:-main}"
}

DEFAULT_BRANCH="$(detect_default)"
CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo HEAD)"

# Detached HEAD — no branch context for a clean-tree review.
if [[ "$CURRENT_BRANCH" == "HEAD" ]]; then
  echo "RESULT: rule=unresolvable hint=detached HEAD; pass -b <ref>"
  exit 2
fi

# Rung 2 — feature branch: what this branch adds vs the default (3-dot base).
if [[ "$CURRENT_BRANCH" != "$DEFAULT_BRANCH" ]]; then
  if mb=$(git merge-base HEAD "$DEFAULT_BRANCH" 2>/dev/null) \
     || mb=$(git merge-base HEAD "origin/$DEFAULT_BRANCH" 2>/dev/null); then
    echo "RESULT: base=$mb target=$TARGET rule=feature-merge-base"
    exit 0
  fi
  if [[ "$(git rev-parse --is-shallow-repository 2>/dev/null || echo false)" == "true" ]]; then
    echo "RESULT: rule=unresolvable hint=shallow clone; run 'git fetch --unshallow'"
    exit 2
  fi
  echo "RESULT: rule=unresolvable hint=no merge-base with $DEFAULT_BRANCH; pass -b <ref>"
  exit 2
fi

# On the default branch.
# Rung 3 — upstream tracking branch.
if up=$(git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null); then
  base=$(git merge-base "$up" HEAD 2>/dev/null || echo "$up")
  echo "RESULT: base=$base target=$TARGET rule=default-upstream"
  exit 0
fi

# Rung 4 — most recent tag.
if tag=$(git describe --tags --abbrev=0 2>/dev/null); then
  base=$(git merge-base "$tag" HEAD 2>/dev/null || echo "$tag")
  echo "RESULT: base=$base target=$TARGET rule=default-tag"
  exit 0
fi

# Rung 5 — previous commit.
if git rev-parse --verify -q 'HEAD~1' >/dev/null 2>&1; then
  echo "RESULT: base=HEAD~1 target=$TARGET rule=default-prev"
  exit 0
fi

# Rung 6 — single commit: diff against the empty tree (all files as added).
EMPTY_TREE="$(git hash-object -t tree /dev/null)"
echo "RESULT: base=$EMPTY_TREE target=$TARGET rule=default-initial"
exit 0
