# Brainstorm: Sample idea

**Date:** 2026-05-21

## Summary

Minimal brainstorm fixture for the apex spec-closure heuristic negative test — this file must NOT trigger spec-closure. The H1 is `# Brainstorm:` rather than the spec marker, and the document carries no workstreams subheader (intentionally omitted from the body so the test's substring match stays clean).

## Recommendation

Try approach A. Reject approach B.

## Risks

- Risk 1 — mitigated by approach A's design.

## Next steps

- Run `/spec -s -f <this path>` to turn the recommendation into workstreams.
