#!/usr/bin/env bash
#
# fetch_commits.sh — emit NUL-delimited commit records between base and HEAD.
#
# Reads the base from `resolve_base.sh` (same precedence ladder the rest of
# the skill uses) unless `-b <ref>` overrides it. Emits one record per
# commit on stdout:
#
#   <sha>\0<subject>\0<body>\0---\n
#
# NUL separators keep commit messages with embedded newlines or shell
# metacharacters intact; the trailing `---\n` lets line-oriented parsers
# find record boundaries without re-counting NULs. Consumed by the
# prose-hygiene lens (subject/body length, AI signature footers,
# conventional-commit shape) and by `scripts/check_prose_hygiene.py
# --commits-file <path>`.
#
# Output also includes a header line so consumers know what they're reading:
#
#   RESULT: base=<ref> commit_count=<N>
#
# Exit:
#   0   resolved and emitted (commit_count may be 0)
#   2   base could not be resolved — passes through from resolve_base.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

BASE_OVERRIDE=""
while getopts ":b:" opt; do
  case "$opt" in
    b) BASE_OVERRIDE="$OPTARG" ;;
    *) echo "RESULT: error=usage: fetch_commits.sh [-b <ref>]" >&2; exit 2 ;;
  esac
done

resolver_args=()
if [[ -n "$BASE_OVERRIDE" ]]; then
  resolver_args=(-b "$BASE_OVERRIDE")
fi

if ! resolver_line=$(bash "$SCRIPT_DIR/resolve_base.sh" "${resolver_args[@]}" 2>/dev/null); then
  # Pass through the resolver's own RESULT line on stdout so the consumer
  # can read the hint without parsing stderr.
  bash "$SCRIPT_DIR/resolve_base.sh" "${resolver_args[@]}" 2>&1 || true
  exit 2
fi

# `resolver_line` shape: `RESULT: base=<ref> target=<ref> rule=<rung>`
base=$(printf '%s\n' "$resolver_line" | sed -n 's/^RESULT: base=\([^ ]*\).*/\1/p')

if [[ -z "$base" ]]; then
  echo "RESULT: error=resolve_base.sh did not emit a base ref" >&2
  exit 2
fi

# `git log <base>..HEAD` excludes <base> itself. Empty result means the
# branch is not ahead of base — emit count=0 and exit 0 (not an error).
count=$(git rev-list --count "${base}..HEAD" 2>/dev/null || echo 0)

echo "RESULT: base=$base commit_count=$count"

if [[ "$count" == "0" ]]; then
  exit 0
fi

# %x00 = NUL byte. Subject (%s) and body (%b) preserve newlines inside the
# body; the NUL between them is the only field separator the consumer
# needs to know about.
git log "${base}..HEAD" --pretty=format:'%H%x00%s%x00%b%x00---%n' --reverse
