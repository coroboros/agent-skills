"""Coherence-graph lens for code-ultrareview.

Six sub-graphs that detect cross-artifact drift: description, version,
capability, cross-reference, example, spec-conformance. Each extractor is a
pure Python 3 stdlib module exporting a `run(repo, ignore, **kwargs)` function
that returns a list of `Finding`s. The orchestrator (`run.py`) composes them
and applies `.coherence-ignore` allowlists.
"""
