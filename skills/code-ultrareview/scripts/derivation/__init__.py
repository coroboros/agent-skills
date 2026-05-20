"""Derivation lens — reconcile planning artifacts against the diff.

The sixth lens in the code-ultrareview family. Activates on `--reconcile`
and compares brainstorm / spec / apex-plan / PR-body / issue-body artifacts
against the diff, classifying divergences as GAP / SCOPE-ADD /
DECISION-OVERRIDE / CONSISTENT.

Public entry: `derivation.run.main` (CLI) and `derivation.run.run` (Python).
"""
