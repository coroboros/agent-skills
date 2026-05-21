# Spec: Sample feature

**Date:** 2026-05-21
**Status:** Draft

## Overview

Minimal spec fixture for testing apex's spec-closure heuristic. The presence of an H1 `# Spec:` line and the `## Workstreams` subheader below should be enough for step-01 to accept the workstream AC verbatim without re-inferring.

## Goals

- Sample goal.

## Non-goals

- Authentication (out of scope for this spike).

## Workstreams

### WS-1: Sample workstream

| Field | Value |
|-------|-------|
| Priority | P0 |
| Complexity | S |
| Depends on | — |

**Description:** Sample workstream used as a fixture.

**Acceptance criteria:**
- [ ] Given a user request, when the handler runs, then it returns 200.
- [ ] Given a malformed request, when the handler runs, then it returns 400.

**Not included:**
- Auth — out of scope per Non-goals.
