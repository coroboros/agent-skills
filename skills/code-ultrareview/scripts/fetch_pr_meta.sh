#!/usr/bin/env bash
#
# fetch_pr_meta.sh — fetch PR metadata for the current branch (prose-hygiene lens).
#
# Detects an open PR for the current branch via `gh pr view` and emits
# parseable `RESULT:` lines plus the PR body on stdout. Used by the
# prose-hygiene lens to check PR title/body against the portable baseline
# (length, AI tells, internal leaks, signature footers, rule-restatement).
#
# Hard gate: requires both `gh` on PATH AND a successful `gh auth status`.
# When either fails, emits `RESULT: pr_found=false` and exits 0 — graceful
# degradation, never a crash that aborts the review.
#
# Output shape (always ends with a sentinel record so consumers can stop reading):
#
#   RESULT: pr_found=true
#   RESULT: pr_number=<n>
#   RESULT: pr_url=<url>
#   RESULT: pr_base=<branch>
#   RESULT: pr_head=<branch>
#   RESULT: pr_title=<single-line title>
#   ---BODY---
#   <multi-line PR body, verbatim>
#   ---END---
#
# When no PR is found (or gh unavailable):
#
#   RESULT: pr_found=false
#   RESULT: hint=<text>
#
# Exit:
#   0   always — `pr_found=true|false` distinguishes states. The lens treats
#       a non-zero exit as a script bug, not a missing PR.

set -euo pipefail

if ! command -v gh >/dev/null 2>&1; then
  echo "RESULT: pr_found=false"
  echo "RESULT: hint=gh CLI not on PATH"
  exit 0
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "RESULT: pr_found=false"
  echo "RESULT: hint=gh not authenticated (run gh auth login)"
  exit 0
fi

# `gh pr view` without an argument resolves to the PR for the current branch.
# JSON keeps title/body intact across embedded characters; jq is part of
# gh's runtime deps so it is safe to rely on it.
if ! payload=$(gh pr view --json number,url,baseRefName,headRefName,title,body 2>/dev/null); then
  echo "RESULT: pr_found=false"
  echo "RESULT: hint=no open PR for the current branch"
  exit 0
fi

number=$(printf '%s' "$payload"  | jq -r '.number')
url=$(printf '%s' "$payload"     | jq -r '.url')
base=$(printf '%s' "$payload"    | jq -r '.baseRefName')
head=$(printf '%s' "$payload"    | jq -r '.headRefName')
title=$(printf '%s' "$payload"   | jq -r '.title' | tr '\n' ' ')
body=$(printf '%s' "$payload"    | jq -r '.body')

echo "RESULT: pr_found=true"
echo "RESULT: pr_number=$number"
echo "RESULT: pr_url=$url"
echo "RESULT: pr_base=$base"
echo "RESULT: pr_head=$head"
echo "RESULT: pr_title=$title"
echo "---BODY---"
printf '%s\n' "$body"
echo "---END---"
